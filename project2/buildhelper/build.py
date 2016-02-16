#!/usr/bin/env python

# For convenience, it is best to use VariantDir with SConscript file
#
# https://bitbucket.org/scons/scons/wiki/VariantDir%28%29
# Note that when you're not using an SConscript file in the src subdirectory,
# you must actually specify that the program must be built from the build/hello.c file
# that SCons will duplicate in the build subdirectory.

import os
import StringIO
import subprocess

import SCons
from SCons.Script import \
    EnsurePythonVersion, ARGUMENTS, GetOption, Help, \
    Environment, Variables, ListVariable, EnumVariable

from . import linkdep
from . import fs
from . import misc

EnsurePythonVersion(2, 7)

g_node_list_type = SCons.Node.NodeList


# Configurations for various build
class BuildConfig(object):
    def __init__(self, variant_dir, cons_vars):
        """
        variant_dir     Path to the variant dir.
        cons_vars       {'construction variable' : value}
        """
        assert isinstance(variant_dir, str)
        assert isinstance(cons_vars, dict)
        self.variant_dir = variant_dir
        self.cons_vars = cons_vars
        pass


class BuildEnv(object):
    """
    Build enviroment for all builds.
    """
    @staticmethod
    def __add_build_vars(env, build_type_names):
        """
        Return Variables instance.
        """
        assert isinstance(env, Environment)
        assert isinstance(build_type_names, list) and len(build_type_names) > 0
        assert all(map(lambda x: isinstance(x, str), build_type_names))
        vs = Variables(None, ARGUMENTS)
        vs.Add(ListVariable(key='build', help='build type', default=build_type_names[0],
                            names=build_type_names, map={}))
        vs.Add(EnumVariable(key='stage', help='build stage', default='compile',
                            allowed_values=('compile', 'link'), map={}, ignorecase=0))
        vs.Update(env)
        Help(vs.GenerateHelpText(env))
        pass

    def __init__(self,
                 src_dir,
                 build_dir,
                 common_construct_vars,
                 bt_cv_pairs):
        """
        src_dir                 source directory
        build_dir               build directory
        common_construct_vars   {construction var : value}
                                Common construction vars for all build versions.
        bt_cv_pairs             [(build type name, construction vars)]
                                Type of construction vars is the same as common_construct_vars
        """
        self.src_dir = src_dir
        self.build_dir = build_dir
        self.static_lib_dirs, self.app_main_srcs = fs.dirs_c_cpp_sources(src_dir)

        self.common_env = Environment(**common_construct_vars)
        self.__add_build_vars(self.common_env, map(lambda (n, _): n, bt_cv_pairs))

        # { build type name : construct vars map }
        # construct vars map { construction var : value }
        self.__bt_cv_map = dict(bt_cv_pairs)

        # { static lib dir : [c/c++ sources] }
        self.__static_lib_srcs_map = {}
        for each in self.static_lib_dirs:
            self.__static_lib_srcs_map[each] = fs.c_cpp_sources(each)
        pass

    def in_compile_stage(self):
        return self.common_env['stage'] == 'compile'

    def in_link_stage(self):
        return self.common_env['stage'] == 'link'

    def static_lib_srcs(self, lib_dir_path):
        """
        Return [static lib source path] with given lib_dir_path.
        The lib_dir_path must be from a valid static_lib_dir, otherwise, raise KeyError.
        """
        return self.__static_lib_srcs_map[lib_dir_path]

    def build_configs(self):
        """
        Return [BuildConfig instance]
        """
        return map(
            lambda bt_name: BuildConfig(
                os.path.join(self.build_dir, bt_name),
                self.__bt_cv_map[bt_name]),
            set(self.common_env['build']))

    def __str__(self):
        """
        Retrn a string which is the statics of this class.
        """
        indent = "    "
        sio = StringIO.StringIO()

        print >> sio, "Static Library Directories and Sources"
        for each_dir in self.static_lib_dirs:
            print >> sio, indent, each_dir

            for each_src in self.static_lib_srcs(each_dir):
                print >> sio, indent * 2, each_src

        print >> sio, "Application Main Sources"
        for each_src in self.app_main_srcs:
            print >> sio, indent, each_src

        return sio.getvalue()


class Build(object):
    """
    Build apps.
    """
    def __init__(self, build_env, build_cfg):
        """
        build_env   A BuildEnv instance.
        build_cfg   A BuildConfig instance.
        """
        self.__build_env = build_env
        self.__build_cfg = build_cfg
        self.__env = self.__build_env.common_env.Clone()
        self.__env.Append(**self.__build_cfg.cons_vars)
        self.__env.VariantDir(self.__build_cfg.variant_dir, self.__build_env.src_dir, duplicate=0)
        pass

    def __to_build_path(self, src_path):
        if isinstance(src_path, str):
            return fs.replace_top_dir(src_path, self.__build_cfg.variant_dir)
        else:
            assert isinstance(src_path, list)
            return map(lambda x: fs.replace_top_dir(x, self.__build_cfg.variant_dir), src_path)

    def build_static_libs(self):
        """
        Return a list of static libraries targets.
        """
        def build_one_static_lib(acc, lib_dir):
            lib_name = os.path.join(lib_dir, os.path.basename(lib_dir))
            static_lib_target = self.__env.StaticLibrary(
                self.__to_build_path(lib_name),
                self.__to_build_path(self.__build_env.static_lib_srcs(lib_dir)))
            assert isinstance(static_lib_target, g_node_list_type)
            acc.extend(static_lib_target)
            return acc

        return reduce(build_one_static_lib, self.__build_env.static_lib_dirs, g_node_list_type())

    @staticmethod
    def __linked_static_lib_targets(app_main_obj_target, static_lib_targets):
        """
        Return [necessary static lib targets]
        app_main_obj_targets    app main obj target node
        static_lib_targets      [static lib target node]
        """
        assert isinstance(static_lib_targets, g_node_list_type)

        app_main_obj_path = str(app_main_obj_target)

        # {lib path : target node}
        lib_path_node_map = dict(map(lambda n: (str(n), n), static_lib_targets))

        ordered_bins = linkdep.resolve(app_main_obj_path, lib_path_node_map.keys())
        return map(lambda p: lib_path_node_map[p],
                   filter(lambda p: p != app_main_obj_path, ordered_bins))

    def build_app_main_objs(self):
        """
        Construct app main source object targets.
        """
        def build_one_app_main_obj(acc, app_main_src):
            app_main_obj = self.__env.Object(self.__to_build_path(app_main_src))
            assert isinstance(app_main_obj, g_node_list_type)
            acc.extend(app_main_obj)
            return acc

        return reduce(build_one_app_main_obj, self.__build_env.app_main_srcs, g_node_list_type())

    def build_apps(self, app_main_obj_targets, static_lib_targets):
        """
        Construct app targets.
        app_main_obj_targets    [app main obj target]
        static_lib_targets      [static library target]
        """
        def build_one_app(acc, app_main_obj):
            app_name, _ = os.path.splitext(str(app_main_obj))

            try:
                necessary_lib_targets = self.__linked_static_lib_targets(app_main_obj, static_lib_targets)
            except subprocess.CalledProcessError as e:
                # With --clean option, ignore the error.
                if self.__env.GetOption('clean'):
                    necessary_lib_targets = []
                else:
                    print e
                    print "Please run scons with 'stage=compile' to compile it."
                    self.__env.Exit(1)

            # Link an app with its specialized libraires
            app_link_env = self.__env.Clone()
            app_link_env.Prepend(LIBS=necessary_lib_targets)
            app_main_target = app_link_env.Program(app_name, app_main_obj)
            assert isinstance(app_main_target, g_node_list_type)
            acc.extend(app_main_target)
            return acc

        return reduce(build_one_app, app_main_obj_targets, g_node_list_type())

    def build(self):
        """
        Return (compile targets, link targets)
        Construct all builds.
        """
        static_lib_targets = self.build_static_libs()
        app_main_obj_targets = self.build_app_main_objs()

        if self.__build_env.in_link_stage():
            self.build_apps(app_main_obj_targets, static_lib_targets)
        pass


def build(src_dir,
          build_dir,
          common_construct_vars,
          bt_cv_pairs):
    """
    src_dir                 source directory
    build_dir               build directory
    common_construct_vars   {consttruction var : value}
                            Common construction vars for all build versions.
    bt_cv_pairs             [(build type name, construction vars)]
                            Type of construction vars is the same as common_construct_vars
    """
    build_env = BuildEnv(src_dir=src_dir,
                         build_dir=build_dir,
                         common_construct_vars=common_construct_vars,
                         bt_cv_pairs=bt_cv_pairs)

    if not GetOption('help'):
        if GetOption('clean'):
            print misc.text_box('Clean')
        else:
            if build_env.in_compile_stage():
                print misc.text_box("Compile")
                print build_env
            else:
                assert build_env.in_link_stage()
                print misc.text_box("Link")

        for each in build_env.build_configs():
            build = Build(build_env, each)
            build.build()

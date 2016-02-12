def FlagsForFile(filename, **kwargs):
    flags = ['-I', 'src',
             '-std=c++11']
    return {'flags': flags,
            'do_cache': True}

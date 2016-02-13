// http://www.codeproject.com/Articles/570638/Ten-Cplusplus11-Features-Every-Cplusplus-Developer
#include <typeinfo>

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <utility>
#include <memory>
#include <algorithm>

using ::std::cout;
using ::std::endl;
using ::std::string;
using ::std::vector;
using ::std::map;
using ::std::make_pair;


////////////
//  auto  //
////////////

template<typename T1, typename T2>
auto compose(T1 t1, T2 t2) -> decltype(t1 + t2) {
    return t1 + t2;
}

void autoFeature() {
    cout << "########" << endl;
    cout << "# auto #" << endl;
    cout << "########" << endl;

    auto i = 42;
    auto l = 42LL;
    auto p = new short();

    cout << "type i: " << typeid(i).name() << endl;
    cout << "type l: " << typeid(l).name() << endl;
    cout << "type p: " << typeid(p).name() << endl;

    map<string, vector<int> > m;
    m.insert(make_pair("abc", vector<int>()));
    for (auto it = begin(m); it != end(m); ++it) {
        cout << "type it: " << typeid(it).name() << endl;
    }

    auto v = compose(2, 3.14);
    cout << "type v: " << typeid(v).name() << endl;
}


///////////////
//  nullptr  //
///////////////
void foo(int *p) {}
void bar(std::shared_ptr<int> p) {}

void nullptrFeature() {
    cout << "###########" << endl;
    cout << "# nullptr #" << endl;
    cout << "###########" << endl;

    int* p1 = NULL;
    int* p2 = nullptr;
    if (p1 == p2) {}

    foo(nullptr);
    bar(nullptr);

    bool f = nullptr;
    // error: cannot convert 'std::nullptr_t' to 'int' in initialization
    // int i = nullptr;
}

/////////////////////////////
//  Ranged-based for loop  //
/////////////////////////////
void rangeBasedForLoop() {
    cout << "######################" << endl;
    cout << "# For-based for loop #" << endl;
    cout << "######################" << endl;

    map<string, vector<int> > m;
    vector<int> v;
    v.push_back(1);
    v.push_back(2);
    v.push_back(3);
    m["one"] = v;

    for (const auto& kvp : m) {
        cout << kvp.first << endl;
        for (auto v : kvp.second) {
            cout << v << endl;
        }
    }

    int arr[] = {1, 2, 3, 4, 5};
    cout << "Original arr[]:" << endl;
    for (const auto& e : arr) {
        cout << "arr[]: " << e << " " << typeid(e).name() << endl;
    }
    for (int& e : arr) {
        e = e * e;
    }
    cout << "Squared arr[]:" << endl;
    for (const auto& e : arr) {
        cout << "arr[]: " << e << " " << typeid(e).name() << endl;
    }
}

//////////////////////////
//  override and final  //
//////////////////////////
class B {
public:
    virtual void f(short) { cout << "B::f" << endl; }
    virtual void h(int) { cout << "B::h" << endl; }
};

class D : public B {
public:
    // This will cause a compile error.
    // error: 'virtual void D::f(int)' marked override, but does not override
    // Because 'void f(int)' not defined in the base class B.
    // virtual void f(int) override { cout << "D::f" << endl; }
    virtual void f(short) override { cout << "D::f" << endl; }
    virtual void h(int) override final { cout << "D::h" << endl; }
};

class E : public D {
public:
    virtual void f(short) override { cout << "E::f" << endl; }
    // This will cause a compile error.
    // error: virtual function 'virtual void E::h(int)'
    // error: overriding final function 'virtual void D::h(int)'
    // Because D::h(short) has been marked with final keyword.
    // virtual void h(int) override { cout << "E::h" << endl; }
};

////////////////////////////
//  Strongly-typed enums  //
////////////////////////////
void stronglyTypedEnumFeature() {
    cout << "#######################" << endl;
    cout << "# Strongly typed enum #" << endl;
    cout << "#######################" << endl;

    enum class Options { None, One, All };
    // For enum class, the type itself is a scope.
    // error: 'All' was not declared in this scope
    // Options o = All;
    Options o = Options::All;
}

//////////////////////
//  Smart Pointers  //
//////////////////////
template<typename P>
void showInt(const char* prefix, P p) {
    cout << prefix << ' ' << *p << endl;
}

void tryUniqPtr() {
    cout << "# uniq_ptr #" << endl;
    std::unique_ptr<int> p1(new int(42));
    std::unique_ptr<int> p2 = std::move(p1); // transfer ownership

    cout << "unique_ptr p1 = " << p1.get() << endl;
    cout << "unique_ptr p2 = " << p2.get() << endl;

    if (p1) {
        showInt("Value from uniqe_ptr p1: ", p1.get());
    }

    (*p2)++;

    if (p2) {
        showInt("Value from unique_ptr p2: ", p2.get());
    }
}

void trySharedPtr() {
    cout << "# shared_ptr #" << endl;
    // There 2 p1 initializations equivalent.
    // Use std::make_shared is recommended, because:
    // 1. Shared object and the smart pointer can be allocated together.
    // 2. Overcome exception after new problem (Exception after new may cause memory leak).
    // std::shared_ptr<int> p1(new int(42));
    auto p1 = std::make_shared<int>(42);
    std::shared_ptr<int> p2 = p1;

    cout << "p1 use count: " << p1.use_count() << endl;
    cout << "p2 use count: " << p2.use_count() << endl;

    (*p1)++;
    showInt("Value from shared_ptr p1: ", p1);
    showInt("Value from shared_ptr p2: ", p2);
}

void tryWeakPtr() {
    cout << "# weak_ptr #" << endl;

    auto p = std::make_shared<int>(42);
    std::weak_ptr<int> wp = p;

    {
        // A weak_ptr instance must be locked before referring to the object.
        auto sp = wp.lock();
        cout << "sp type: " << typeid(sp).name() << endl;
        cout << "sp = " << sp << endl;
        cout << "*sp = " << *sp << endl;
    }

    p.reset();
    cout << "after reset p" << endl;
    cout << "p = " << p << endl;
    if (wp.expired()) {
        cout << "expired" << endl;
    }
}

void smartPointerFeature() {
    cout << "#################" << endl;
    cout << "# Smart Pointer #" << endl;
    cout << "#################" << endl;

    tryUniqPtr();
    trySharedPtr();
    tryWeakPtr();
}

//////////////
//  Lambda  //
//////////////
void lambdaFeature() {
    cout << "##########" << endl;
    cout << "# Lambda #" << endl;
    cout << "##########" << endl;

    vector<int> v;
    v.push_back(1);
    v.push_back(2);
    v.push_back(3);

    cout << "All numbers:" << endl;
    std::for_each(std::begin(v), std::end(v), [](int n) { cout << n << endl; });

    auto is_odd = [](int n) { return n % 2 == 1; };
    auto pos = std::find_if(std::begin(v), std::end(v), is_odd);
    if (pos != std::end(v)) {
        cout << "Got odd number: " << *pos << endl;
    }

    std::function<int(int)> fib = [&fib](int n) { return n < 2 ? 1 : fib(n - 1) + fib(n - 2); };
    cout << "fib(5) = " << fib(5) << endl;
}

////////////////////////////////
//  non-member begin() end()  //
////////////////////////////////
// std::begin() and std::end() works for both STL containerss and arrays;
void nonMemberBeginEndFeature() {
    cout << "############################" << endl;
    cout << "# Non-member begin() end() #" << endl;
    cout << "############################" << endl;

    int v[] = {1, 2, 3};

    cout << "All numbers:" << endl;
    std::for_each(std::begin(v), std::end(v), [](int n) { cout << n << endl; });

    auto is_odd = [](int n) { return n % 2 == 1; };
    auto pos = std::find_if(std::begin(v), std::end(v), is_odd);
    if (pos != std::end(v)) {
        cout << "Got odd number: " << *pos << endl;
    }
}

/////////////////////////////////////
//  static_assert and type traits  //
/////////////////////////////////////
template<typename T, size_t N>
class Vec {
    static_assert(N < 3, "Size is too large");
    T _points[N];
};

// This will cause error on static_assert
// src/cxx11.cc: In instantiation of 'class Vec<int, 3ul>':
// src/cxx11.cc:289:13:   required from here
// src/cxx11.cc:285:5: error: static assertion failed: Size is too large
//      static_assert(N < 3, "Size is too large");
//           ^
// Vec<int, 3> v1;
Vec<int, 2> v2;

template<typename T1, typename T2>
auto add(T1 t1, T2 t2) -> decltype(t1 + t2) {
    return t1 + t2;
}

void staticAssertTypeTraitsFeature() {
    cout << "#############################" << endl;
    cout << "# static_assert type_traits #" << endl;
    cout << "#############################" << endl;

    cout << add(1, 3.14) << endl;
    cout << add("one", 2) << endl;
}

int main() {
    autoFeature();
    nullptrFeature();
    rangeBasedForLoop();
    stronglyTypedEnumFeature();
    smartPointerFeature();
    lambdaFeature();
    nonMemberBeginEndFeature();
    staticAssertTypeTraitsFeature();

    return 0;
}

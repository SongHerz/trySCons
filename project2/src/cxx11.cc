#include <typeinfo>

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <utility>
#include <memory>

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

int main() {
    autoFeature();
    nullptrFeature();
    rangeBasedForLoop();

    return 0;
}

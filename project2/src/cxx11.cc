#include <typeinfo>

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <utility>

using ::std::cout;
using ::std::endl;
using ::std::string;
using ::std::vector;
using ::std::map;
using ::std::make_pair;

template<typename T1, typename T2>
auto compose(T1 t1, T2 t2) -> decltype(t1 + t2) {
    return t1 + t2;
}

////////////
//  auto  //
////////////
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

int main() {
    autoFeature();

    return 0;
}

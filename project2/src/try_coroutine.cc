#include <iostream>
#include <algorithm>
#include <boost/coroutine/all.hpp>


void coroutineFabonacci() {
	boost::coroutines::asymmetric_coroutine<int>::pull_type source(
		[&](boost::coroutines::asymmetric_coroutine<int>::push_type& sink) {
			int first = 1, second = 1;
			sink(first);
			sink(second);
			for (int i = 0; i < 9; ++i) {
				  int third = first + second;
				  first = second;
				  second = third;
				  sink(third);
			}
		 });

    for(auto i: source) {
        std::cout << i << " ";
    }
    std::cout << std::endl;
}


void coroutinePushDataToHandler() {
	struct FinalEOL {
		~FinalEOL() {
			std::cout << std::endl;
		}
	};  // End of struct FinalEOL

	const int num=5, width = 15;
	boost::coroutines::asymmetric_coroutine<std::string>::push_type writer(
		[&](boost::coroutines::asymmetric_coroutine<std::string>::pull_type& in) {
			// finish the last line when we leave by whatever means
			FinalEOL eol;
			// pull values from upstream, lay themout 'num' to a line
			for (;;) {
				for (int i = 0; i < num; ++i) {
					if (!in) return;
					std::cout << std::setw(width) << in.get();
					// Now, advance to next item.
					in();	// This will cause a context switch
				}
				std::cout << std::endl;
			}
        });

	std::vector<std::string> words {
		"peas", "porridge", "hot", "peas",
		"porridge", "cold", "peas", "porridge",
		"in", "the", "pot", "nine",
		"days", "old" };

	std::copy(boost::begin(words), boost::end(words), boost::begin(writer));
}


int main() {
	std::cout << "Running Fabonaccci (coroutine) ..." << std::endl;
	coroutineFabonacci();
	std::cout << std::endl;

	std::cout << "push data to handler (coroutine) ..." << std::endl;
	coroutinePushDataToHandler();
	std::cout << std::endl;
    return 0;
}


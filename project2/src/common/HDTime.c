#include "HDTime.h"

#include <stdio.h>
#include <time.h>

void showTime() {
    const time_t t = time(NULL);
    printf("%s %s\n", __FUNCTION__, ctime(&t));
}

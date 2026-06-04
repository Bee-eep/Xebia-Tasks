#include <iostream>
#include <vector>
using namespace std;

int main() {
    vector<int> arr = {12, 35, 1, 10, 34, 1};

    int largest = arr[0];

    for (int i = 1; i < arr.size(); i++) {
        if (arr[i] > largest) {
            largest = arr[i];
        }
    }

    int secondLargest = -1;

    for (int i = 0; i < arr.size(); i++) {
        if (arr[i] != largest && arr[i] > secondLargest) {
            secondLargest = arr[i];
        }
    }

    cout << secondLargest;

    return 0;
}
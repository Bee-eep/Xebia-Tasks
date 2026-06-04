#include <iostream>
#include <unordered_map>
#include <string>
using namespace std;

int main() {
    string s;
    cin >> s;

    unordered_map<char, int> mp;

    int start = 0;
    int maxLen = 0;

    for (int end = 0; end < s.length(); end++) {
        if (mp.find(s[end]) != mp.end() && mp[s[end]] >= start) {
            start = mp[s[end]] + 1;
        }

        mp[s[end]] = end;

        int len = end - start + 1;

        if (len > maxLen) {
            maxLen = len;
        }
    }

    cout << maxLen;

    return 0;
}
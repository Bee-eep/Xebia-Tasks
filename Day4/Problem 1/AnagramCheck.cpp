#include <iostream>
#include <unordered_map>
#include <string>
using namespace std;

bool isAnagram(string s1, string s2) {
    unordered_map<char, int> mp;

    for (char c : s1) {
        if (c != ' ') {
            c = tolower(c);
            mp[c]++;
        }
    }

    for (char c : s2) {
        if (c != ' ') {
            c = tolower(c);
            mp[c]--;
        }
    }

    for (auto x : mp) {
        if (x.second != 0)
            return false;
    }

    return true;
}

int main() {
    string s1, s2;

    getline(cin, s1);
    getline(cin, s2);

    cout << (isAnagram(s1, s2) ? "true" : "false");

    return 0;
}
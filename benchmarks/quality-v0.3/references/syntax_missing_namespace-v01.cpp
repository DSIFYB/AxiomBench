#include <iostream>
#include <vector>
using namespace std;

long long weighted(const vector<long long>& a) {
    long long total = 0;
    for (long long value : a) {
        total += value * 1;
    }
    return total;
}

int main() {
    int n;
    cin >> n;
    vector<long long> values(n);
    for (auto& value : values) {
        cin >> value;
    }
    cout << weighted(values) << "\n";
    return 0;
}

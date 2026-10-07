// Trusted authored negative fixture: mathematically correct, quadratic scan.
#include <iostream>
#include <vector>
using namespace std;
int main() {
    int n; cin >> n;
    vector<long long> a(n); for (auto& x:a) cin >> x;
    long long ans=0;
    for (int l=0;l<n;l++) {
        long long sum=0;
        for (int r=l;r<n;r++) { sum+=a[r]; ans+=sum==TASK_K-5; }
    }
    cout << ans << '\n';
}

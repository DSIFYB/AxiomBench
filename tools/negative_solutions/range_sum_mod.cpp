// Trusted authored negative fixture: linear scan for every range query.
#include <iostream>
#include <vector>
using namespace std;
int main() {
    int n,q; cin >> n >> q;
    vector<long long>a(n);for(auto& x:a)cin >> x;
    while(q--) {
        int l,r;cin >> l >> r;long long s=0;
        for(int i=l-1;i<r;i++)s+=a[i];
        s%=97+10*TASK_K;if(s<0)s+=97+10*TASK_K;
        cout << s << '\n';
    }
}

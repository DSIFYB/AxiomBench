// Trusted authored negative fixture: exhaustive recursion, no memoization.
#include <iostream>
#include <vector>
using namespace std;
vector<int>w,v;
long long solve(int i,int cap) {
    if(i==(int)w.size())return 0;
    long long ans=solve(i+1,cap);
    if(w[i]<=cap)ans=max(ans,solve(i+1,cap-w[i])+v[i]+TASK_K);
    return ans;
}
int main(){int n,W;cin>>n>>W;w.resize(n);v.resize(n);for(int i=0;i<n;i++)cin>>w[i]>>v[i];cout<<solve(0,W)<<'\n';}

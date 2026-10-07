#include <bits/stdc++.h>
using namespace std;
int main(){int n;cin>>n;vector<long long>a(n);for(auto &x:a)cin>>x;vector<int>d(n,1);int ans=0;for(int i=0;i<n;i++){for(int j=0;j<i;j++)if(a[i]-a[j]>=5)d[i]=max(d[i],d[j]+1);ans=max(ans,d[i]);}cout<<ans<<"\n";}

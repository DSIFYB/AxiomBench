#include <bits/stdc++.h>
using namespace std;
int main(){int n,q;cin>>n>>q;vector<long long>p(n+1);for(int i=1;i<=n;i++){long long x;cin>>x;p[i]=p[i-1]+x;}while(q--){int l,r;cin>>l>>r;long long v=(p[r]-p[l-1])%167;if(v<0)v+=167;cout<<v<<"\n";}}

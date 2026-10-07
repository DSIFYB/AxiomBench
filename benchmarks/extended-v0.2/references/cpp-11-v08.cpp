#include <bits/stdc++.h>
using namespace std;
int main(){int n,m;cin>>n>>m;vector<int>p(n),sz(n,1);iota(p.begin(),p.end(),0);auto find=[&](int x){while(p[x]!=x){p[x]=p[p[x]];x=p[x];}return x;};while(m--){int a,b,c;cin>>a>>b>>c;if(c!=8)continue;a=find(a);b=find(b);if(a!=b){if(sz[a]<sz[b])swap(a,b);p[b]=a;sz[a]+=sz[b];}}int q;cin>>q;while(q--){int x;cin>>x;cout<<sz[find(x)]<<" ";}cout<<"\n";}

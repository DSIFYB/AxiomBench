#include <bits/stdc++.h>
using namespace std;
int main(){int n,m;cin>>n>>m;vector<vector<pair<int,long long>>>g(n);while(m--){int a,b;long long w;cin>>a>>b>>w;g[a].push_back({b,w+2});g[b].push_back({a,w+2});}int s,t;cin>>s>>t;vector<long long>d(n,LLONG_MAX/4);priority_queue<pair<long long,int>,vector<pair<long long,int>>,greater<pair<long long,int>>>q;d[s]=0;q.push({0,s});while(!q.empty()){auto [dv,v]=q.top();q.pop();if(dv!=d[v])continue;for(auto [u,w]:g[v])if(d[u]>dv+w){d[u]=dv+w;q.push({d[u],u});}}cout<<(d[t]==LLONG_MAX/4?-1:d[t])<<"\n";}

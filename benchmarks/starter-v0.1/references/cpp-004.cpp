#include <bits/stdc++.h>
using namespace std;
int main(){int n,m;cin>>n>>m;vector<vector<int>>g(n+1);while(m--){int a,b;cin>>a>>b;g[a].push_back(b);g[b].push_back(a);}int s,t;cin>>s>>t;vector<int>d(n+1,-1);queue<int>q;d[s]=0;q.push(s);while(!q.empty()){int v=q.front();q.pop();for(int u:g[v])if(d[u]<0){d[u]=d[v]+1;q.push(u);}}cout<<d[t]<<'\n';}

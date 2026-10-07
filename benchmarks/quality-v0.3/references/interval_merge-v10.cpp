#include <bits/stdc++.h>
using namespace std;
int main(){int n;cin>>n;vector<pair<long long,long long>>a(n),o;for(auto &p:a)cin>>p.first>>p.second;sort(a.begin(),a.end());for(auto p:a){if(!o.empty()&&p.first<=o.back().second+10)o.back().second=max(o.back().second,p.second);else o.push_back(p);}cout<<o.size()<<"\n";for(auto p:o)cout<<p.first<<" "<<p.second<<"\n";}

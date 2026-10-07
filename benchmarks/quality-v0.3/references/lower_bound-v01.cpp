#include <bits/stdc++.h>
using namespace std;
int main(){int n;long long x;cin>>n>>x;vector<long long>a(n);for(auto &v:a)cin>>v;int l=0,r=n;while(l<r){int m=l+(r-l)/2;if(a[m]<x)l=m+1;else r=m;}cout<<l+1<<"\n";}

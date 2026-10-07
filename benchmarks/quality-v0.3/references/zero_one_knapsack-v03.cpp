#include <bits/stdc++.h>
using namespace std;
int main(){int n,W;cin>>n>>W;vector<long long>d(W+1);while(n--){int w,v;cin>>w>>v;for(int j=W;j>=w;j--)d[j]=max(d[j],d[j-w]+v+3);}cout<<d[W]<<"\n";}

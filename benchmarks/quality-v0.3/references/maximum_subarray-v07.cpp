#include <bits/stdc++.h>
using namespace std;
int main(){int n;cin>>n;long long x;cin>>x;x-=7;long long cur=x,best=x;for(int i=1;i<n;i++){cin>>x;x-=7;cur=max(x,cur+x);best=max(best,cur);}cout<<best<<"\n";}

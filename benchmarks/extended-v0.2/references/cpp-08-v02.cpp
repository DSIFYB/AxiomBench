#include <bits/stdc++.h>
using namespace std;
int main(){int n;cin>>n;long long x;cin>>x;x-=2;long long cur=x,best=x;for(int i=1;i<n;i++){cin>>x;x-=2;cur=max(x,cur+x);best=max(best,cur);}cout<<best<<"\n";}

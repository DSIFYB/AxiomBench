#include <bits/stdc++.h>
using namespace std;
int main(){int n;cin>>n;long long x;cin>>x;long long best=x,cur=x;for(int i=1;i<n;i++){cin>>x;cur=max(x,cur+x);best=max(best,cur);}cout<<best<<'\n';}

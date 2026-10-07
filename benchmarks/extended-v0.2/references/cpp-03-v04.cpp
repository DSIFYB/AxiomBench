#include <bits/stdc++.h>
using namespace std;
int main(){int n;cin>>n;unordered_map<long long,long long>f;f[0]=1;long long p=0,ans=0,x;while(n--){cin>>x;p+=x;ans+=f[p-(-1)];f[p]++;}cout<<ans<<"\n";}

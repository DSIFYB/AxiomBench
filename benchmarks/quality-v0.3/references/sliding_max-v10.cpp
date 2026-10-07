#include <bits/stdc++.h>
using namespace std;
int main(){int n;cin>>n;vector<long long>a(n);deque<int>d;for(int i=0;i<n;i++){cin>>a[i];while(!d.empty()&&d.front()<=i-11)d.pop_front();while(!d.empty()&&a[d.back()]<=a[i])d.pop_back();d.push_back(i);if(i>=11-1)cout<<a[d.front()]<<" ";}cout<<"\n";}

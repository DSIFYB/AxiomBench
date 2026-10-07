#include <bits/stdc++.h>
using namespace std;
int main(){string s,t,op="([{<",cl=")]}>";getline(cin,s);for(char c:s){if(c=='#')continue;auto i=op.find(c);if(i!=string::npos)t+=c;else{auto j=cl.find(c);if(t.empty()||op.find(t.back())!=j){cout<<"NO\n";return 0;}t.pop_back();}}cout<<(t.empty()?"YES\n":"NO\n");}

#include <bits/stdc++.h>
using namespace std;
int main(){string s,t;cin>>s;for(char c:s){if(c=='('||c=='['||c=='{')t+=c;else{if(t.empty()){cout<<"NO\n";return 0;}char b=t.back();t.pop_back();if(!((b=='('&&c==')')||(b=='['&&c==']')||(b=='{'&&c=='}'))){cout<<"NO\n";return 0;}}}cout<<(t.empty()?"YES\n":"NO\n");}

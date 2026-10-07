#include <bits/stdc++.h>
using namespace std;
int main(){string a,b;getline(cin,a);getline(cin,b);int n=a.size(),m=b.size();vector<vector<int>>d(n+1,vector<int>(m+1));for(int i=0;i<=n;i++)d[i][0]=i*2;for(int j=0;j<=m;j++)d[0][j]=j*2;for(int i=1;i<=n;i++)for(int j=1;j<=m;j++)d[i][j]=min({d[i-1][j]+2,d[i][j-1]+2,d[i-1][j-1]+(a[i-1]!=b[j-1])});cout<<d[n][m]<<"\n";}

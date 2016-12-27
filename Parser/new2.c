#include<stdio.h>
double x[200],y[200];
int n,m;
int main()
{
	int i;
	n=100;
	for (i=0; i<n; i++) {
		int if_test;
		y[i] = 0.0f;
		x[i] = i+1;
		if (i>n/2)
		{
			if_test=1;
		}
	}
	return 0;
}

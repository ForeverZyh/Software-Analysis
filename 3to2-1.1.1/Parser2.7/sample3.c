#include<stdio.h>
double x[200],y[200];
int n,m;
void validate()
{
	int i;
	for(i=0;i<n;i++)
		printf("%.4lf %.4lf\n",x[i],y[i]);
}
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
			break;
		}
	}
	for (i=0; i<n; i++) {
          y[i] = 2.0f * x[i] + y[i];
    }
	validate();
	return 0;
}

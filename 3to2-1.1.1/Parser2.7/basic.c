#include<stdio.h>
float b[110][110],a[110],n;
void validate()
{
	int i;
	for(i=0;i<n;i++) printf("%.4lf\n",a[i]);
}
int main()
{
    int i,j,x,y,k;
    n=100;

    for(i=0;i<n;i++) a[i]=i;

    for(i=0;i<n;i++) x=a[i];

    for(i=0;i<n;i++) x=x+a[i];

    for(i=0;i<n;i++) a[i]=i;
    y=i;

    for(i=0;i<n;i++) a[i]=a[i]+1;

    for(i=0;i<n;i++) a[i]=a[i+1];

    for(i=0;i<n;i++)
    {
        float sum;
		sum=0;
        for(j=0;j<n;j++)
        {
            b[i][j]=a[j];
            sum=sum+b[i][j];
        }
        for(j=0;j<n;j++) a[j]=sum/100;
    }
	validate();
	return 0;
}

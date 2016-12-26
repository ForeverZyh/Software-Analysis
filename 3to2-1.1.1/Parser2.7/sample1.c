#include<stdio.h>
double A[110][110],Anew[110][110],error,n,m,tol;
int iter;
void validate()
{
	int i,j;
	for(i=1;i<n;i++)
		for(j=1;j<m;j++) printf("%.4lf\n",A[i][j]);
}
int main()
{
	int i,j,iter_max;
	iter_max=100;
	n=100;
	m=100;
	error=1;
	tol=0.00001;
	for(i=1;i<n;i++)
		for(j=1;j<m;j++) Anew[i][j]=i*1.0/j;
	while ( error > tol && iter < iter_max ) {
		error = 0.0;
		for(  j = 1; j < n; j++) {
			for( i=1;i < m;i++) {
				A[j][i] = 0.25 * ( Anew[j][i+1] + Anew[j][i-1] + Anew[j-1][i] + Anew[j+1][i]);
				error = fmax( error, fabs(A[j][i] - Anew[j][i]));
			}
		}
		for(  j = 1; j < n; j++) {
			for(  i = 1; i < m; i++ ) {
				Anew[j][i] = A[j][i];
			} 
		}
		iter++;
	}
	validate();
	return 0;
}

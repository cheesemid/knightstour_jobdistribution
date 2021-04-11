#include <stdio.h>
#include <stdlib.h>

int rcounter = 0;
void printarr(int *arr){
	int i, j;
	for (i = 0; i < 8; i++){
		for (j = 0; j < 8; j++){
			if ( *(arr + i*8 + j) < 10){
				printf(" ");
			}
			printf("%d ", *(arr + i*8 + j));
		}
		printf("\n");
	}
}
int knight(int startx, int starty, int iteration, int *visited, int *allmovesrelative){
	*(visited + startx*8 + starty) = iteration;
	rcounter++;
	if (iteration == 64){
		printarr(visited);
		return 0;
	}
	int i;
	for (i = 0; i < 16; i+=2){
		int testx = startx + *(allmovesrelative + i);
		int testy = starty + *(allmovesrelative + i + 1);
		if (testx >= 0 && testx <= 7 && testy >= 0 && testy <= 7 && *(visited + testx*8 + testy) == 0){
			if (knight(testx,testy,iteration+1,visited,allmovesrelative) == 0){
				return 0;
			}
		}
	}
	*(visited + startx*8 + starty) = 0;
	return 1;
}
int main(int argc, char *argv[]){
	int x = 0;
	int y = 0;
	int i = 0;
	if (argc == 3){
		x = atoi(argv[2]);
		y = atoi(argv[1]);
	}
	int* visited = (int *)malloc(8 * 8 * sizeof(int));
	for (i = 0; i < 64; i++) {
		*(visited + i) = 0; // thanks to malloc not initializing memory
	}
	int allmovesrelative[16] = { -1,2,1,2,2,1,1,-2,2,-1,-2,-1,-2,1,-1,-2 };
	knight(x,y,1,visited,allmovesrelative);
	printf("%d\n", rcounter);
	return 0;
}


// 7f,6f -> move 7 to 0, move 6 to 0

// og : {-2,1,-1,2,1,2,2,1,1,-2,2,-1,-1,-2,-2,-1} fast 3,3 4,4
// 6 first : {-1,-2,-2,1,-1,2,1,2,2,1,1,-2,2,-1,-2,-1}
// 7 first : {-2,-1,-2,1,-1,2,1,2,2,1,1,-2,2,-1,-1,-2} fast 0,0 0,1; 14s 7,7
// 7f,6f,7f : {-1,-2,2,-1,-2,-1,-2,1,-1,2,1,2,2,1,1,-2}
// 7f,6f : {-1,-2,-2,-1,-2,1,-1,2,1,2,2,1,1,-2,2,-1}
// 3f,6f : {-1,-2,2,1,-2,1,-1,2,1,2,1,-2,2,-1,-2,-1}

//[1, 2, 3, 4, 5, 7, 0, 6] : {-1,2,1,2,2,1,1,-2,2,-1,-2,-1,-2,1,-1,-2} FASTEST 0,0 2ms

// 1,0 {-2,-1,2,-1,2,1,1,-2,-1,-2,-1,2,1,2,-2,1}
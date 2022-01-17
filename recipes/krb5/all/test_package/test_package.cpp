#include "krb5.h"
#include <stdio.h>

int main() {
  krb5_context ctx;

  if (krb5_init_context(&ctx) != 0) {
    printf("krb5_init_context returned an error\n");
    return 1;
  }

  krb5_free_context(ctx);
  printf("Test passed.");
  return 0;
}

####### BAYBHIN GURUNG #########
####### BSGURUNG #########
####### 113224953 #########

.data
msg: .asciiz "This is a test program in mips\n"


.text
.globl hw0_main
hw0_main:
#
 la $a0, msg
 li $v0, 4
 syscall

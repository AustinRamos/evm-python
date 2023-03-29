

def push2(ctx): 
    
    two_bytes = ctx.read_code(2)
    ctx.stack.push(two_bytes)

 
 #read abotu how stack works againnn
def push4(ctx):
    four_bytes = ctx.read_code(4)
    ctx.stack.push(four_bytes)

def push6(ctx):
    six_bytes = ctx.read_code(6)
    ctx.stack.push(six_bytes)

def push10(ctx):
    ten_bytes = ctx.read_code(10)
    ctx.stack.push(ten_bytes)

def push11(ctx):
    eleven_bytes = ctx.read_code(11)
    ctx.stack.push(eleven_bytes)

def push32(ctx):
    thirty_two_bytes = ctx.read_code(32)
    ctx.stack.push(thirty_two_bytes)

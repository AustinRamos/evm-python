

def push2(ctx): 
    print("INSIDE helpers.py: " , ctx.stack.stack)
    print(2)
    two_bytes = ctx.read_code(2)
    ctx.stack.push(two_bytes)

 


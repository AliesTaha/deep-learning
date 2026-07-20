# Prompt:
# Implement an in-memory key-value store with transaction support. It should expose the following operations:
# set(key, value) — set a key to a value
# get(key) — return the value for a key, or null/None if it doesn't exist
# delete(key) — remove a key
# begin() — start a new transaction
# commit() — commit the current transaction
# rollback() — abort the current transaction, discarding its changes

# Requirements:
# Transactions can be nested. If I call begin() twice, then rollback(), only the inner transaction's changes are discarded; 
# the outer transaction is still active.

# commit() on a nested transaction folds its changes into the parent transaction 
# — not into the global store — until the outermost transaction commits.

# Reads inside a transaction must see that transaction's uncommitted writes (read-your-own-writes), 
# and fall through to outer transactions / the global store for keys it hasn't touched.

# commit() or rollback() with no active transaction should raise an error.

# Deletes inside a transaction need to work correctly too — if a transaction deletes a key that exists in the global store, 
# a get inside that transaction returns null, but the key comes back if you roll back.

# Language of your choice. Before you write any code — talk me through your approach. What's your core data structure for the transaction state, and how does get resolve a key?

# (That last question isn't decoration — the delete-inside-a-transaction case is where the naive design breaks. 
# Think about what a transaction layer needs to record to distinguish "I deleted this key" from "I never touched this key.")

# design:
# almost like a git diff
# only storing what needs to be inserted and deleted on a stack and pushing/popping based on that

import threading 

class KVStore:
    def __init__(self, ):
        self.state={}
        self.lock= threading.Lock()
    
    def session(self,):
        return Session(self)

    def commit_diff(self, kv_dic, deleted):
        with self.lock:
            new_state=dict(self.state) # the frozen state we commiting to
            for k in deleted:
                new_state.pop(k)
            for k, v in kv_dic.items():
                new_state[k]=v
            self.state=new_state

class Session:
    def __init__(self, store):
        self.kvstack=[] # stack of k,v dics of inserted elements
        self.deleted=[] # stack of keys that have been deleted
        self.store=store
        self.global_dic = store.state

    def check_in_begin(self, ):
        if not self.kvstack:
            raise

    def set(self, k, v):
        self.check_in_begin()
        latest_dic=self.kvstack[-1]
        latest_dic[k]=v

    def get(self, key):
        #global?
        if not self.kvstack:
            print(f'the answer is {self.global_dic.get(key, None)}')
            return self.global_dic.get(key, None)
        
        #there is a kvstack, we need replay logic on gets
        curr_dic=self.global_dic.copy()
        for i in range(len(self.kvstack)):
            deleted_set=self.deleted[i]
            kv_dic=self.kvstack[i]
            for k_ in deleted_set:
                if k_ in curr_dic:
                    del curr_dic[k_]
            for k,v in kv_dic.items():
                curr_dic[k]=v
        
        #replay complete, curr_dic is latest state
        print(f'the answer is {curr_dic.get(key, None)}')
        return curr_dic.get(key, None)

    def delete(self, k):
        self.check_in_begin()
        latest_dic=self.kvstack[-1] 
        # if key in current temp stack, delete it from there
        # else, add it to the deleted set
        # this way, i'm assuming all deletes were before the writes 
        latest_dic=self.kvstack[-1]
        latest_set=self.deleted[-1]
        if k in latest_dic:
            del latest_dic[k] #just to make sure it doesnt get added after
        latest_set.add(k)
        
    def begin(self, ):
        #beginning a new set of kv and deletes
        self.kvstack.append({})
        self.deleted.append(set())

    def commit(self, ):
        # roll this into the previous one
        if len(self.kvstack)==0:
            raise Exception("no active transaction")
        
        #commit to global
        if len(self.kvstack)==1:
            deleted=self.deleted.pop() #set of deleted k's
            kv_dic=self.kvstack.pop() #set of kv pairs to insert
            # dic=self.global_dic
            # for k in deleted:
            #     if k in dic:
            #         del dic[k]
            # for k,v in kv_dic.items():
            #     dic[k]=v
            self.store.commit_diff(kv_dic, deleted)
            self.global_dic=self.store.state
            print('we were rolled')
        
        #commit to prev
        if len(self.kvstack)>=2:
            deleted=self.deleted.pop() #set of deleted k's
            kv_dic=self.kvstack.pop() #set of kv pairs to insert
            
            prev_dic=self.kvstack[-1]
            prev_del=self.deleted[-1]
            for k in deleted:
                if k in prev_dic:
                    del prev_dic[k]
                prev_del.add(k)
            for k,v in kv_dic.items():
                prev_dic[k]=v

    def rollback(self, ):
        if len(self.kvstack)==0:
            raise
        #just pop last diffs
        self.deleted.pop()
        self.kvstack.pop()

my_kv_store=KVStore()
sesh1=my_kv_store.session()
sesh2=my_kv_store.session()
sesh1.begin()
sesh2.begin()
sesh1.set('ali', 5)
sesh2.set('ali', 22)
sesh2.get('ali')
sesh2.commit()
sesh1.delete('ali')
sesh1.get('ali')
sesh1.commit()
sesh1.get('ali')


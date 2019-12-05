i=0; 
for f in *.abstract; 
do 
    d=chunk_$(printf %d $((i % 100))); 
    mkdir -p $d; 
    mv "$f" $d; 
    let i++; 
done
i=0; 
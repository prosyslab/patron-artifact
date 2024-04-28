rm -rf patron-experiment
git clone https://github.com/prosyslab/patron-experiment
cd patron-experiment
rm -rf patron
rm -rf sparrow
git clone https://github.com/prosyslab/patron
git clone https://github.com/prosyslab/sparrow-incubator
mv sparrow-incubator sparrow
cd patron
opam switch patron-4.13.1
eval $(opam env)
make
cd ../sparrow
git checkout patron
opam switch sparrow-4.13.1+flambda
eval $(opam env)
make
cd ../..
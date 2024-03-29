pushd "${BASH_SOURCE%/*}"

. ./work/secrets.sh

python3 update_counter.py

git add docs/index.html
git add docs/ventes-boutique.html
git commit -m "Mise à jour des compteurs"
git push

popd
pushd "${BASH_SOURCE%/*}"

. ../helloasso/work/secrets.sh

python3 stage.py --refresh

git add docs/index.html
git add docs/ventes-boutique.html
git commit -m "Mise à jour des compteurs"
git push

popd
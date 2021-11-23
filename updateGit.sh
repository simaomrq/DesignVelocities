##############################################################################
### adapted from:
### https://www.freecodecamp.org/news/automate-project-github-setup-mac/
###
### 2021-05-20 
### Simao Marques
#############################################################################


# step 1: set the absolute path to your repo directory
TARGETDIR=/users/sm0087/parallel_scratch/CADbasedOptimisation/DesignVelocities

REPO_NAME="DesignVelocities"
DESCRIPTION="Git File exchange"

echo "name of your remote repo: ${REPO_NAME} "
echo "Repo description: ${DESCRIPTION}"

echo "Absolute path to your local project directory: ${TARGETDIR}"

# step 2: Add your github username & password:
USERNAME="simaomrq"	## change username
PASSW="testpassw"	## add your password

git config --global user.name "${USERNAME}"
git config --global user.email your_email@here

# step 3 : go to path 
cd "$TARGETDIR"

# step 4: initialise the repo locally, create blank README, add and commit
git init
git pull

# step 5: set up files you want to add/update to repo, replace test with "surface_positions.dat"
git add surface_sens_cd.csv surface_sens_cl.csv
git commit -m 'new sens test commit with .sh script'

#  step 6 add the remote github repo to local repo and push
git remote add origin https://github.com/${USERNAME}:${PASSW}/${REPO_NAME}.git
git push --set-upstream origin main

# step 7 change to your project's root directory.
cd "$TARGETDIR"

echo "Done. Go to https://github.com/$USERNAME/$REPO_NAME to see." 
echo " *** You're now in your project root. ***"

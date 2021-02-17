#!/bin/bash
echo "Installer for PASTA database on Ubuntu Systems"
echo "IMPORTANT: if you have problems, visit https://jugit.fz-juelich.de/s.brinckmann/pasta_python/-/wikis/notesUser"
echo "The following actions are executed in this script (only install if item does not exist)"
echo "  - install Python 3"
echo "  - install Python extensions: openCV, pip"
echo "  - install pandoc"
echo "  - install git and git-annex; if git is not configured it will be"
echo "  - ensure that xv command exists"
echo "  - install couchDB"
echo "  - adopt PATH and PYTHONPATH"
echo "  - clone python programs for micromechanics"
echo "  - clone python backend of PASTA"
echo "  - clone graphical frontend of PASTA"
echo "  - install python requirements for PASTA"
echo "  - adopt .pasta.json file in home directory"
echo "  - run a short test"
echo "  - install npm (node package manager)"
echo "  - install node requirements for PASTA"
echo "  - start graphical user interface (GUI)"
echo
read -p "Do you wish to install all these items now [Y/n] ? " yesno
if [[ $yesno = 'N' ]] || [[ $yesno = 'n' ]]
then
  echo "  Did not install anything"
  exit
fi
echo

echo "Ensure installer has sudo rights"
if [ "$EUID" -ne 0 ]
  then
  echo "  ERROR: Please run as root with 'sudo ./install.sh' "
  exit
fi
echo
THEUSER=$(logname)


echo "Ensure python is installed"
OUTPUT=$(python3 --version)
IFS=' ' read -ra OUTPUT1 <<< "$OUTPUT"
IFS='.' read -ra OUTPUT2 <<< "${OUTPUT1[1]}"
if [ ${OUTPUT1[0]} = "Python" ] && [ ${OUTPUT2[0]} = "3" ]
then
  echo "  Python installed in version 3."
else
  echo "  Info: Python 3 will be installed."
  sudo apt-get install -y python3
fi
echo
echo "Ensure openCV for python is installed"
if dpkg --get-selections | grep -q "^python3-opencv[[:space:]]*install$" >/dev/null
then
  echo "  python3-opencv is installed"
else
  echo "  Info: Python-OpenCV will be installed."
  sudo apt-get install -y python3-opencv
fi
echo
echo "Ensure pip for python is installed"
if dpkg --get-selections | grep -q "^python3-pip[[:space:]]*install$" >/dev/null
then
  echo "  python3-pip is installed"
else
  echo "  Info: Python3-pip will be installed."
  sudo apt-get install -y python3-pip
fi
echo


echo "Ensure pandoc is installed"
if command -v pandoc &> /dev/null
then
  echo "  pandoc installed."
else
  echo "  Info: pandoc will be installed."
  sudo apt-get install -y pandoc
fi
echo
echo "Ensure git is installed"
if command -v git &> /dev/null
then
  echo "  git installed."
else
  echo "  Info: git will be installed."
  sudo apt-get install -y git
fi
echo
echo "Ensure git-annex is installed"
if command -v git-annex &> /dev/null
then
  echo "  git-annex installed."
else
  echo "  Info: git-annex will be installed."
  sudo apt-get install -y git-annex
fi
OUTPUT=$(sudo -u $THEUSER git config -l | grep "user")
if [[ -n $OUTPUT ]]
then
  echo "  git user and email are set"
else
  echo "  Set your git user information"
  read -p "  What is your name? " GIT_NAME
  read -p "  What is your email? " GIT_EMAIL
  sudo -u $THEUSER git config --global --add user.name "${GIT_NAME}"
  sudo -u $THEUSER git config --global --add user.email $GIT_EMAIL
fi
echo


echo "Ensure xv works, which is required for python-pillow"
if command -v xv &> /dev/null
then
  echo "  xv is present"
else
  echo "  xv is not present. Try display"
  if ! command -v display &> /dev/null
  then
    echo "  xv and display are NOT installed. Imagemagick will be installed."
    sudo apt-get install -y imagemagick
  fi
  echo "  Create link from display to xv."
  sudo ln -s /usr/bin/display /usr/bin/xv
fi
echo


echo "Ensure couchdb is installed"
if dpkg --get-selections | grep -q "^couchdb[[:space:]]*install$" >/dev/null
then
  echo "  couchdb is installed"
else
  echo "Install instructions:"
  echo "  choose Standalone installation. Rest: choose OK"
  echo "  The password and username are scrambled at first usage, hence not stored as plain-text. Both are in a vault."
  sudo apt-get install -y gnupg ca-certificates
  echo "deb https://apache.bintray.com/couchdb-deb focal main" | sudo tee /etc/apt/sources.list.d/couchdb.list
  sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 8756C4F765C9AC3CB6B85D62379CE192D401AB61
  sudo apt update
  sudo apt install -y couchdb
fi
CDB_USER="admin"
read -p "  Which password did you enter? " CDB_PASSW
echo


echo "Two empty (for safety) directories are required. One for the source code"
echo "and the other as central place to store data, work in."
read -p "  Where to store the source code? [pasta_source, i.e. /home/${THEUSER}/pasta_source] " pasta_src
read -p "  Where to store the data? [pasta, i.e. /home/${THEUSER}/pasta] " pasta
read -p "  What is your user id, e.g. orcid-id. Only small letters [random_user] ? " pasta_user
if [ -z $pasta_src ]
then
  pasta_src="pasta_source"
fi
if [ -z $pasta ]
then
  pasta="pasta"
fi
if [ -z $pasta_user ]
then
  pasta_user="random_user"
fi
sudo -u $THEUSER mkdir /home/$THEUSER/$pasta_src
sudo -u $THEUSER mkdir /home/$THEUSER/$pasta_src/pasta_tutorial
sudo -u $THEUSER mkdir /home/$THEUSER/$pasta
echo


echo "Start cloning the git repositories: tools, python-backend, javascript-frontend"
cd /home/$THEUSER/$pasta_src
sudo -u $THEUSER git clone https://jugit.fz-juelich.de/s.brinckmann/experimental-micromechanics.git
sudo -u $THEUSER git clone https://jugit.fz-juelich.de/s.brinckmann/pasta_python.git
sudo -u $THEUSER git clone https://jugit.fz-juelich.de/s.brinckmann/pasta_electron.git
echo


echo "Adopt path and python-path in your environment"
sudo -u $THEUSER echo "#PASTA changes" >> /home/$THEUSER/.bashrc
sudo -u $THEUSER echo "export PATH=\$PATH:/home/${THEUSER}/${pasta_src}/pasta_python" >> /home/$THEUSER/.bashrc
sudo -u $THEUSER echo "export PYTHONPATH=\$PYTHONPATH:/home/${THEUSER}/${pasta_src}/pasta_python" >> /home/$THEUSER/.bashrc
sudo -u $THEUSER echo "export PYTHONPATH=\$PYTHONPATH:/home/${THEUSER}/${pasta_src}/experimental-micromechanics" >> /home/$THEUSER/.bashrc
echo


echo "Install python requirements"
cd /home/$THEUSER/$pasta_src/pasta_python
cd /home/$THEUSER/$pasta_src/pasta_python
sudo -H pip3 install -r requirements.txt
echo


echo "Create PASTA configuration file .pasta.json in home directory"
sudo -u $THEUSER echo "{" > /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "  \"-userID\": \"${pasta_user}\"," >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "  \"-defaultLocal\": \"pasta_tutorial\"," >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "  \"-defaultRemote\": \"remote\"," >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "  \"-eargs\": {\"editor\": \"emacs\", \"ext\": \".org\", \"style\": \"all\"}," >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "  \"-magicTags\": [\"P1\",\"P2\",\"P3\",\"TODO\",\"WAIT\",\"DONE\"]," >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "  " >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "  \"local\": {" >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "    \"user\": \"${CDB_USER}\"," >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "    \"password\": \"${CDB_PASSW}\"," >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "    \"database\": \"${pasta_user}\"," >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "    \"path\": \"${pasta}\"" >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "  }," >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "  " >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "  \"pasta_tutorial\": {" >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "    \"user\": \"${CDB_USER}\"," >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "    \"password\": \"${CDB_PASSW}\"," >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "    \"database\": \"pasta_tutorial\"," >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "    \"path\": \"${pasta_src}/pasta_tutorial\"" >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "  }," >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "  " >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "  \"remote\": {" >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "    \"user\": \"____\"," >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "    \"password\": \"____\"," >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "    \"url\": \"https://____\"," >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "    \"database\": \"____\"" >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "  }," >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "  " >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "  \"-tableFormat-\": {" >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "    \"project\":{\"-label-\":\"Projects\",\"-default-\": [22,6,50,22]}," >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "    \"measurement\":{\"-default-\": [24,7,23,23,-5,-6,-6,-6]}," >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "    \"sample\":{\"-default-\": [23,23,23,23,-5]}," >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "    \"procedure\":{\"-default-\": [20,20,20,40]}" >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "  }" >> /home/$THEUSER/.pasta.json
sudo -u $THEUSER echo "}" >> /home/$THEUSER/.pasta.json
echo


echo "Run a very short test for 5sec?"
cd /home/$THEUSER/$pasta_src/pasta_python
sudo PYTHONPATH=/home/$THEUSER/$pasta_src/pasta_python:/home/$THEUSER/$pasta_src/experimental-micromechanics/src -u $THEUSER python3 pastaDB.py test
echo
echo 'If this test is not successful, it is likely that you entered the wrong username'
echo "  and password. Open the file /home/$THEUSER/.pasta.json with an editor and correct"
echo '  the entries after "user" and "password". "-userID" does not matter. Entries under'
echo '  "remote" do not matter, either.'
echo
echo "Run a short test for 20-40sec?"
sudo PYTHONPATH=/home/$THEUSER/$pasta_src/pasta_python:/home/$THEUSER/$pasta_src/experimental-micromechanics/src -u $THEUSER python3 Tests/testTutorial.py
echo


echo "Graphical user interface GUI"
echo "  Ensure npm is installed"
if command -v npm &> /dev/null
then
  echo "  npm installed."
else
  echo "  Info: npm will be installed."
  sudo apt-get install -y npm
fi
echo
cd /home/$THEUSER/$pasta_src/pasta_electron
sudo -u $THEUSER npm install


echo -e "\033[0;31m=========================================================="
echo -e "Last step: Start the graphical user interface. If you want to do that in "
echo -e "the future:"
echo -e "  cd /home/$THEUSER/$pasta_src/pasta_electron"
echo -e "  npm start"
echo -e "During the first run of the GUI, click 'Test Backend' in CONFIGURATION. It"
echo -e "is good to start with Projects, then Samples and Procedures and finally"
echo -e "Measurements."
echo -e "==========================================================\033[0m"
echo
sudo PATH=$PATH:/home/$THEUSER/$pasta_src/pasta_python -u $THEUSER npm start

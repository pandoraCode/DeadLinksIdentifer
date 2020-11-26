#!/bin/bash
#- Créer un script bash qui utilise votre projet
#- le script bash doit accepter un url vers un repertoire git en argument.
#- le script bash doit accepter un argument pour indiquer le port ou rouler le programme et la variable d'environnement PORT
#	- le script bash doit cloner le git, installer les dépendence node (npm install)
#	- le script bash doit partir le serveur node localement (npm start) en spécifiant le port (la variable d'environnement se nomme PORT)
# - le script bash doit exécuter votre programme sur le serveur node local (http://localhost) en vérifiant le bon port.
# - provided link: https://github.com/stevenvachon/broken-link-checker.git
# - a link can run npm start https://github.com/johntango/npmExpress.git

github=""
# we provide an error port at the beginning
port=

help_msg="nodeinstaller.sh -g [github repository] -p [port]"
#lack_git_url_msg="please use nodeinstaller.sh -g [url] to specify a git repository"
no_argument_msg="no argument provided"
lack_git_url_msg="please provide a git url"
lack_valid_url_msg="please provide a valid git url"
lack_valid_port_msg="please provide a valid port"


process_git() {

    echo "git url: $1, port: $2"
#    # install python dependency
    pip3 install -r requirements.txt

    # check repo existence before git clone
    repo_folder="$(basename "$1" .git)"
    echo "repoFolder:::: $repo_folder:::::"
    if [ ! -d "$repo_folder" ];
    then
      git clone $1
    else
      echo "$repo_folder"
    fi

    # pre state: kill node server when terminate
    trap "kill 0" EXIT

    # start server
    cd "$repo_folder"
    npm install
    npm start -- --port $2 &
    sleep 5

    # run python script
    cd ..
    localhost_url="http://localhost:$2"
    python3 "scrapper.py" -u "$localhost_url"
#    wait
}

#
#process_normal() {
#  # install python dependency
#    pip3 install -r requirements.txt
#    echo "-----------------"
#    echo $all_arguments
#    echo "-----------------"
#    # prepare crawl
#    if is_argument_appear "-c" || is_argument_appear "--crawl"
#    then
#       # run python script
#       python3 "scrapper.py" $all_arguments
#    else
#       # run python script
#       python3 "scrapper.py" $all_arguments -c on
#    fi
#
#
#
#}

# make the error message shown in red color
echo_err() {
  echo -e "\033[1;31m ERROR! "$1" \033[0m"
  echo "$help_msg"
}


## check if specific arguments appear
is_argument_appear() {
  if [[ " ${all_arguments[@]} " =~ " $1 " ]]
  then
    return 0
  else
    return 1
  fi
}



# std:err append to std:out
is_valid_git_url() {
  output=$((git ls-remote --exit-code -h "$1") 2>&1)
  # include error message
  if [[ "$output" = *fatal* ]]
  then
    echo_err "$lack_valid_url_msg"
    return 1
  else
    # reuturn true
    return 0
  fi
}

# check if port is valid
is_valid_port() {
  # if port is a number
  if [ "$1" -gt 0 ] 2>/dev/null
  then
    # if port is a number in [0, 65535]
    if (($1>=0 && $1<=65535))
    then
      return 0
    else
      echo_err "$lack_valid_port_msg"
      return 1
    fi
  else
    echo_err "$lack_valid_port_msg"
    return 1
  fi
}

# no arguments provided in arguments
has_arguments() {
  if [ $1 -eq 0 ]
  then
    echo_err "$no_argument_msg"
    return 1
  else
    # pass 0 for true
    return 0
  fi
}


# get all arguments
all_arguments="$@"

# parse params
if has_arguments $#
then
  while [[ "$#" > 0 ]]; do case $1 in
    -h|--help) break ; shift;shift;;
    -g|--git) github="$2";shift;shift;;
    -p|--port) port="$2";shift;shift;;
    *) shift; shift;;
  esac; done

  echo "$all_arguments"
  # if help needed,
  if is_argument_appear "-h" || is_argument_appear "--help"
  then
    echo "$help_msg"
  # if help not needed
  else
    # if -g or --git appears in arguments
    if is_argument_appear "-g" || is_argument_appear "--git"
    then
      echo "github: $github, port: $port"
      if is_valid_git_url "$github"
      then
        if is_valid_port "$port"
        then
          echo "correct~~~ github: $github, correct~~~ port: $port"
          process_git "$github" "$port"
        fi
      fi
    # if no git url provided
    # pass all the arguments to python script
#    else
#      process_normal
    fi
  fi
fi
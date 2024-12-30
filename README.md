# Smarttri de Viveris

## Description
Smarttri est une application mobile innovante conçue pour faciliter le tri des déchets grâce à la reconnaissance des produits via leur code-barres. En utilisant la caméra du smartphone, l'application scanne le code-barres des objets et fournit instantanément des informations sur la poubelle à choisir pour ce déchet. L'objectif est de simplifier le processus de gestion des déchets, de sensibiliser les utilisateurs à la nécessité de trier efficacement et de réduire l'impact environnemental.

## Installation

### Prérequis
- [Docker](https://www.docker.com/) doit être installé sur votre machine.
- [Postman](https://www.postman.com/) doit être installé sur votre machine

### Étapes pour démarrer le projet avec Docker

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/Saadiinho/viveris.git
   cd viveris

2. Construire l'image Docker :
   ```bash
   docker build -t smarttri-api .
 
3. Lancer un conteneur basé sur cette image :
   ```bash
   docker run -d -p 8000:8000 smarttri-api

5. Lancer Postman pour tester les différents requêtes de cette API 

## Les différents endpoints

Pour l'instant, seul deux endpoints sont disponibles : 
1. L'inscription :
   ```bash
   POST https://localhost:8000/api/users/sign-up/

2. La connexion :
   ```bash
   POST https://localhost:8000/api/users/sign-in/

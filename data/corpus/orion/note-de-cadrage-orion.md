# Projet ORION — Note de cadrage

Compte rendu de la réunion de lancement du 3 mars 2026. Diffusion : équipe projet, comité de direction de Méridian Logistique. Version 1.2, validée le 12 mars 2026.

## 1. Contexte

Méridian Logistique est une entreprise de transport et d'entreposage de 1 180 salariés, répartis sur 14 sites en France. Le service support interne (IT, RH, moyens généraux) traite environ 2 300 demandes par mois via l'outil de ticketing. Le délai moyen de première réponse est de 31 heures. Une enquête interne de novembre 2025 montre que 62 % des demandes portent sur des questions déjà documentées dans l'intranet, mais que les collaborateurs ne trouvent pas l'information.

Le projet ORION consiste à mettre en place un assistant conversationnel interne capable de répondre aux questions courantes des collaborateurs à partir de la documentation existante, et de créer un ticket qualifié lorsqu'une intervention humaine est nécessaire.

## 2. Gouvernance

- Sponsor : Hélène Vasseur, directrice des opérations.
- Chef de projet : Karim Benali, responsable du service support.
- Référent technique : Sophie Lemaire, architecte data.
- Référent sécurité : Thomas Rouvière, RSSI.
- Équipe de réalisation : 2 développeurs internes, 1 prestataire data science à mi-temps.

Le comité de pilotage se réunit toutes les trois semaines. Les décisions d'architecture sont prises par le référent technique après avis du référent sécurité.

## 3. Périmètre

Périmètre du pilote (phase 1) :

- questions IT de niveau 1 : mots de passe, accès aux applications, matériel, VPN ;
- questions RH : congés, notes de frais, mutuelle, télétravail ;
- création de ticket qualifié dans l'outil existant lorsque l'assistant ne peut pas répondre.

Hors périmètre du pilote : les questions relatives à la paie individuelle, les demandes des sites en Belgique et en Espagne, et toute action de modification dans le système d'information (réinitialisation de mot de passe, création de compte). Ces actions sont envisagées en phase 2.

## 4. Décisions d'architecture

Décision D1 : le modèle de langage est accédé par API auprès d'un fournisseur hébergeant les données dans l'Union européenne. Aucun modèle n'est entraîné ni ajusté sur les données internes pendant la phase 1.

Décision D2 : la base documentaire est indexée dans une base vectorielle Qdrant, déployée sur l'infrastructure interne. Les documents sources restent dans l'intranet, seule la copie indexée est dans Qdrant. L'index est reconstruit chaque nuit.

Décision D3 : toute réponse de l'assistant cite le document source. Une réponse sans source identifiée n'est pas affichée ; l'assistant propose alors la création d'un ticket.

Décision D4 : les conversations sont conservées 90 jours à des fins d'amélioration, puis supprimées. Les collaborateurs en sont informés au premier usage.

## 5. Budget et calendrier

Budget de la phase 1 : 185 000 euros, dont 120 000 euros de prestation externe, 40 000 euros de coûts d'infrastructure et de consommation API sur douze mois, et 25 000 euros de conduite du changement.

Jalons :

- 3 mars 2026 : lancement.
- 15 juin 2026 : ouverture du pilote à 150 collaborateurs volontaires du site de Lyon-Saint-Priest.
- 30 septembre 2026 : comité de décision go / no-go pour le déploiement à l'ensemble des sites français.
- Janvier 2027 : déploiement général si la décision est favorable.

## 6. Indicateurs de succès

Le pilote est considéré comme réussi si, à la date du comité go / no-go :

- au moins 60 % des demandes soumises à l'assistant sont résolues sans création de ticket ;
- le délai de première réponse pour les tickets créés par l'assistant est inférieur à 8 heures ;
- le taux de réponses signalées comme incorrectes par les utilisateurs est inférieur à 5 % ;
- le score de satisfaction des utilisateurs du pilote est supérieur ou égal à 4 sur 5.

## 7. Risques identifiés

| Risque | Probabilité | Impact | Mesure |
|---|---|---|---|
| Documentation intranet obsolète ou contradictoire | Élevée | Élevé | Revue documentaire de 6 semaines avant l'indexation, pilotée par le service support |
| Réponses inexactes sur les questions RH | Moyenne | Élevé | Validation des réponses RH par la DRH sur un jeu de 200 questions avant ouverture du pilote |
| Faible adoption par les collaborateurs | Moyenne | Moyen | Communication interne, ambassadeurs sur le site pilote |
| Dépassement du budget API | Faible | Moyen | Plafond de consommation mensuel de 2 500 euros, alerte à 80 % |

## 8. Prochaines étapes

- Constitution du jeu de 200 questions de validation avant le 31 mars 2026 (responsable : Karim Benali).
- Revue documentaire du 16 mars au 24 avril 2026.
- Choix du fournisseur LLM avant le 15 avril 2026 (responsable : Sophie Lemaire).
- Point sécurité et conformité RGPD le 28 avril 2026 (responsable : Thomas Rouvière).

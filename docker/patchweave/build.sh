docker pull rshariffdeen/patchweave:experiments
docker run -it --memory=30g --name patchweave rshariffdeen/patchweave:experiments
docker cp patchweave:proof_for_wrong_patches /
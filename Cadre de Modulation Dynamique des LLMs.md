## 1. Cadre Général – Modulation Dynamique dans un Espace de Surface

Soit :

- $\mathcal{M}$ : le modèle LLM (non modifié dans ses poids)
- $\mathcal{S} = \{ s_i(t) \}$ : un ensemble de modules dynamiques, chacun avec un état $s_i \in \mathbb{R}$
- $\Phi$ : le comportement observable généré par $\mathcal{M}$ sous contrainte de $\mathcal{S}$
- $\Sigma$ : le cadre de surface conceptuelle construit (ex. prompts dynamiques)
- $\mathcal{T}$ : la tension de cohérence locale mesurée à chaque pas de génération

On a :

$$
\Phi(t) = \mathcal{M}[\Sigma(\mathcal{S}(t))]
$$

et

$$
\frac{ds_i}{dt} = f_i(s_i, t) + \sum_j \rho_{ij} \cdot g_{ij}(s_j(t - \delta_{ij}))
$$

---

## 2. Tension de Cohérence – Métrique Opératoire

La tension locale de cohérence $\tau_{c,i}$ est définie par :

$$
\tau_{c,i}(t) = \frac{|I_i(t) - O_i(t)|}{|I_i(t)| + \varepsilon}
$$

- $I_i(t)$ : entrée conceptuelle projetée sur le module
- $O_i(t)$ : activation produite dans la réponse
- $\varepsilon$ : constante de stabilisation (ex. $10^{-10}$)

Agrégation globale :

$$
\bar{\tau}_c(t) = \frac{1}{N} \sum_i \tau_{c,i}(t)
$$

---

## 3. Émergence Stabilisée – Attracteurs et Transitions de Phase

### Définition

Un comportement $B$ est dit *émergent stabilisé* s’il satisfait :

1. *Répétabilité* : comportements récurrents sous classes de prompts équivalents  
2. *Dépendance de l’état* : dépend de $\mathcal{S}$ et de son évolution  
3. *Résilience* : résistance aux perturbations faibles de l'entrée

### Attracteurs comportementaux

$$
A \subset \Phi \quad \text{tel que} \quad \forall \Phi_0 \in A, \exists t > 0 : \Phi(t) \in A
$$

### Transitions de phase

Lorsque certains seuils sont franchis ($\rho_{ij}$, $s_i$, $\frac{ds}{dt}$), le système passe à une nouvelle phase comportementale (observable par un saut dans $\bar{\tau}_c$ ou une mutation discursive).

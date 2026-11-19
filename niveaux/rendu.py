"""Rendu SVG sans bibliothèque graphique externe."""

from html import escape

from niveaux.grille import ARRIVEE, DEPART, SOL, Niveau


def rendre_svg(niveau: Niveau, titre="Niveau de plateforme"):
    taille = 28
    marge = 32
    haut = 100
    largeur = max(720, niveau.largeur * taille + 2 * marge)
    hauteur = haut + niveau.hauteur * taille + 72
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largeur} {hauteur}" role="img" aria-labelledby="titre description">',
        f'<title id="titre">{escape(titre)}</title>',
        '<desc id="description">Niveau en tuiles. Départ bleu, arrivée orange, sol vert et brun.</desc>',
        f'<rect width="{largeur}" height="{hauteur}" rx="16" fill="#f9f8f3"/>',
        '<g font-family="Segoe UI, Arial, sans-serif" fill="#233f38">',
        '<text x="32" y="29" font-size="11" letter-spacing="2">GÉNÉRATION DE NIVEAUX 2D</text>',
        f'<text x="32" y="61" font-size="23" font-weight="600">{escape(titre)}</text>',
        f'<text x="32" y="82" font-size="12" fill="#60776f">{niveau.largeur} colonnes × {niveau.hauteur} lignes</text>',
        f'<rect x="{marge}" y="{haut}" width="{niveau.largeur * taille}" height="{niveau.hauteur * taille}" fill="#dcefe9"/>',
    ]
    for y, ligne in enumerate(niveau.lignes):
        for x, tuile in enumerate(ligne):
            px, py = marge + x * taille, haut + y * taille
            if tuile == SOL:
                elements.append(f'<rect x="{px}" y="{py}" width="28" height="28" fill="#937453" stroke="#806448" stroke-width="0.5"/>')
                if y == 0 or niveau.lignes[y - 1][x] != SOL:
                    elements.append(f'<rect x="{px}" y="{py}" width="28" height="6" fill="#43846b"/>')
            elif tuile in (DEPART, ARRIVEE):
                couleur = "#347ab1" if tuile == DEPART else "#b9582b"
                elements.extend([
                    f'<rect x="{px + 4}" y="{py + 2}" width="20" height="24" rx="6" fill="{couleur}"/>',
                    f'<text x="{px + 14}" y="{py + 19}" text-anchor="middle" font-size="13" font-weight="700" fill="white">{tuile}</text>',
                ])
    bas = haut + niveau.hauteur * taille
    elements.extend([
        f'<text x="32" y="{bas + 29}" font-size="12">D · Départ     A · Arrivée     ■ Sol</text>',
        f'<text x="32" y="{bas + 50}" font-size="11" fill="#60776f">Vue du terrain — franchissabilité non vérifiée</text>',
        '</g></svg>',
    ])
    return "\n".join(elements)

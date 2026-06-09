import pytest
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


def pytest_addoption(parser):
    parser.addoption(
        '--sqlalchemy_url',
        action='store',
        default='sqlite:///:memory:',
        help='SQLAlchemy connection url to database under test.'
    )


@pytest.fixture()
def engine(request):
    engine = create_engine(
        request.config.getoption('--sqlalchemy_url'),
        echo=True,
    )

    return engine


@pytest.fixture()
def session_maker(request, engine):
    _session_maker = sessionmaker(
        bind=engine
    )

    return _session_maker


def create_data(session):
    from skosprovider.sqlalchemy.models import (
        Concept,
        ConceptScheme,
        Collection,
        Label,
        Note,
        Match,
        Language
    )
    en = session.get(Language, 'en')
    nl = session.get(Language, 'nl')
    cs = ConceptScheme(
        id=1,
        uri='urn:x-skosprovider:test',
        languages=[en, nl]
    )
    session.add(cs)
    con = Concept(
        id=10,
        uri='urn:x-skosprovider:test:1',
        concept_id=1,
        conceptscheme=cs
    )
    session.add(con)
    l = Label('Churches', 'prefLabel', 'en')
    con.labels.append(l)
    l = Label('Kerken', 'prefLabel', 'nl')
    con.labels.append(l)
    col = Collection(
        id=20,
        uri='urn:x-skosprovider:test:2',
        concept_id=2,
        conceptscheme=cs
    )
    col.broader_concepts.add(con)
    n = Note(
        'Churches organised by function, as opposed to by shape or religion.',
        'scopeNote',
        'en'
    )
    col.notes.append(n)
    l = Label('Churches by function', 'prefLabel', 'en')
    col.labels.append(l)
    l = Label('111sortmefirst', 'sortLabel', 'en')
    col.labels.append(l)
    session.add(col)
    chap = Concept(
        id=30,
        uri='urn:x-skosprovider:test:3',
        concept_id=3,
        conceptscheme=cs
    )
    l = Label('Chapels', 'prefLabel', 'en')
    chap.labels.append(l)
    session.add(chap)
    chap.related_concepts.add(con)
    tchap = Concept(
        id=50,
        uri='urn:x-skosprovider:test:5',
        concept_id=5,
        conceptscheme=cs
    )
    tchap.labels.append(Label('Boomkapellen', 'prefLabel', 'nl'))
    session.add(tchap)
    tchap.broader_concepts.add(chap)
    cath = Concept(
        id=40,
        uri='urn:x-skosprovider:test:4',
        concept_id=4,
        conceptscheme=cs
    )
    l = Label('Cathedrals', 'prefLabel', 'en')
    cath.labels.append(l)
    n = Note(
        'A cathedral is a church which contains the seat of a bishop.',
        'definition',
        'en'
    )
    cath.notes.append(n)
    match = Match(
        matchtype_id='closeMatch',
        uri='http://vocab.getty.edu/aat/300007501'
    )
    cath.matches.append(match)
    session.add(cath)
    cath.member_of.add(col)
    pchurch = Concept(
        id=60,
        uri='urn:x-skosprovider:test:6',
        concept_id=6,
        conceptscheme=cs
    )
    l = Label('Parochiekerken', 'prefLabel', 'nl')
    pchurch.labels.append(l)
    session.add(pchurch)
    pchurch.member_of.add(col)
    hkerk = Concept(
        id=70,
        uri='urn:x-skosprovider:test:7',
        concept_id=7,
        conceptscheme=cs
    )
    l = Label('Hulpkerken', 'prefLabel', 'nl')
    hkerk.labels.append(l)
    session.add(hkerk)
    hkerk.broader_concepts.add(pchurch)
    chparts = Collection(
        id=80,
        uri='urn:x-skosprovider:test:8',
        concept_id=8,
        conceptscheme=cs,
        infer_concept_relations=False
    )
    l = Label('Parts of churches', 'prefLabel', 'en')
    chparts.labels.append(l)
    session.add(chparts)
    chparts.broader_concepts.add(con)
    chtow = Concept(
        id=90,
        uri='urn:x-skosprovider:test:9',
        concept_id=9,
        conceptscheme=cs,
    )
    l = Label('Churchtowers', 'prefLabel', 'en')
    chtow.labels.append(l)
    match = Match(
        matchtype_id='exactMatch',
        uri='http://vocab.getty.edu/aat/300003625'
    )
    chtow.matches.append(match)
    session.add(chtow)
    chtow.member_of.add(chparts)
    session.commit()


def create_visitation(session):
    from skosprovider.sqlalchemy.utils import (
        VisitationCalculator
    )
    from skosprovider.sqlalchemy.models import (
        Visitation,
        ConceptScheme
    )
    vc = VisitationCalculator(session)
    conceptschemes = session.execute(select(ConceptScheme)).scalars().all()
    for cs in conceptschemes:
        visit = vc.visit(cs)
        for v in visit:
            vrow = Visitation(
                conceptscheme=cs,
                concept_id=v['id'],
                lft=v['lft'],
                rght=v['rght'],
                depth=v['depth']
            )
            session.add(vrow)
    session.commit()

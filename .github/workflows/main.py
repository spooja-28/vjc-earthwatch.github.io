import json
import os
from base64 import b64decode

import gspread
from dotenv import load_dotenv


load_dotenv('.github/workflows/.env')

#### SECRETS should be stored in a .env file or saved as an environment variable
#### Look at .env.example

START_PLANT_GRID = '<!-- <<< START PLANT GRID >>> -->'
END_PLANT_GRID = '<!-- <<< END PLANT GRID >>> -->'


class InvalidFormatting(Exception):
    """Raised when Unable to parse google sheet file due to an invalid format"""
    def __init__(self):
        super().__init__('Unable to parse google sheet file due to an invalid format')


def get_sheet_data(creds, sheet_id):
    """Authenticates with Google Sheets and returns
    an iterator over the worksheet data

    Parameters
    ----------
    creds: Dict
        Dictionary generated from Google Developers Console
        that provides access to a service account
    sheet_id: str
        String representation of a Google Sheet ID

    Returns
    -------
    Worksheet Data: Iterator[Dict]
        Keys: Name, Scientific Name, Description, Plant Type, Lifespan, Spread, Plant Height,
              Toxicity Level (0-5), Toxicity, Flower Color, Bloom Time, Flower Size, Country of Origin
    """

    gc = gspread.service_account_from_dict(creds)
    sheet = gc.open_by_key(sheet_id)

    for ws in sheet.worksheets():
        all_data = ws.get_all_records(head=2)  # first row contains instructional data that should be ignored
        # list of objects {
        #   Name, Scientific Name, Description, Plant Type, Lifespan, Spread, Plant Height,
        #   Toxicity Level (0-5), Toxicity, Flower Color, Bloom Time, Flower Size, Country of Origin
        # }

        print(f'Retrieved {ws.title}')
        for n in range(len(all_data)):
            all_data[n]['Location'] = ws.title.split(' (')[0].lower().replace(' ', '_').replace('@', '').replace('__', '_')

        yield all_data


def parse_data(index, data, template):
    """Returns a filled up HTML-template with the plant metadata

    Parameters
    ----------
    data: Dict
        Keys: Name, Scientific Name, Description, Location, Plant Type, Lifespan, Spread, Plant Height,
              Toxicity Level (0-5), Toxicity, Flower Color, Bloom Time, Flower Size, Country of Origin

    Returns
    -------
    HTML Template: str
    """
    return template.format(
        index=index,
        name=data['Name'].strip().title(),
        sci_name=data['Scientific Name'].strip().title(),
        location=data['Location'],
        description=data['Description'].strip(),
        bloom_time=data['Bloom Time'].strip(),
        country=data['Country of Origin'].strip(),
        toxicity=data['Toxicity'].strip(),
        lifespan=data['Lifespan'].strip(),
        spread=data['Spread'].strip(),
        height=data['Plant Height'].strip()
    )


def main():
    with open('.github/workflows/template.html') as f:
        template = f.read().replace('\n', '')

    google_creds = json.loads(b64decode(os.environ['GOOGLE_CREDS']))  # env var will be a stringified base64encoded credentials
    plants = {}
    for ws in get_sheet_data(google_creds, os.environ['SHEET_ID']):
        plant_grid = ['<div class="plant-grid">', ' ' * 4 + '<r-grid columns=5>']
        plant_information = ['<div class="plant-information">']

        for n, i in enumerate(ws):
            compulsory_keys = [
                'Name', 'Scientific Name', 'Description', 'Location', 'Plant Type', 'Lifespan', 'Spread', 'Plant Height',
                'Toxicity Level (0-5)', 'Toxicity', 'Flower Color', 'Bloom Time', 'Flower Size', 'Country of Origin'
            ]
            if any(x not in i for x in compulsory_keys): raise InvalidFormatting
            # parse data and produce html
            plant_grid.append(' ' * 8 + f'<r-cell><a class="h-8" href="#plant-{n}"><img src="assets/{i["Location"]}/{n}.jpg" class="hw-8 cover"></a></r-cell>')
            plant_information.append(' ' * 4 + parse_data(n, i, template))

        plant_grid.append(' ' * 4 + '</r-grid>')
        plant_grid.append('</div>')
        plant_information.append('</div>')

        with open(f'{i["Location"]}.html', 'r+', encoding='utf8') as f:
            content = f.read()

            split_data = [i.strip() for i in content.splitlines()]
            start_index = split_data.index(START_PLANT_GRID)
            end_index = split_data.index('<!-- <<< END PLANT GRID >>> -->')

            new_content = content.splitlines()[:start_index + 1] + plant_grid + [''] + plant_information + content.splitlines()[end_index:]

            f.seek(0)
            f.write('\n'.join(new_content))

        plants[i["Location"]] = ws

    with open('assets/plants.json', 'w', encoding='utf8') as f:
        json.dump(plants, f)


if __name__ == '__main__':
    main()
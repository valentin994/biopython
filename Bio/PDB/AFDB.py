"""Toolset for accessing alphahold database for bulk downloads and possibly more"""

import argparse
import asyncio
from pprint import pprint

import httpx


class AFDB:
    """
    TODO
    """

    def __init__(
        self,
        ftp_server: str = "https://ftp.ebi.ac.uk/pub/databases/alphafold",
        version: str = "latest",
    ) -> None:
        """TODO"""
        self.ftp_server = ftp_server
        self.version = version
        self.api_client = httpx.AsyncClient()

    async def get_readme(self) -> str:
        """TODO"""
        try:
            request_readme = await self.api_client.get(f"{self.ftp_server}/README.txt")
            request_readme.raise_for_status()
        except httpx.HTTPStatusError as err:
            return f"Exception occured for fetching the README. {err}"
        except httpx.RequestError as err:
            return f"Error occurred during the request: {err}"
        return request_readme.text

    async def get_metadata_json(self) -> dict | str:
        """TODO"""
        try:
            request_metadata = await self.api_client.get(
                f"{self.ftp_server}/download_metadata.json"
            )
        except httpx.HTTPStatusError as err:
            return f"Exception occured for fetching the README. {err}"
        except httpx.RequestError as err:
            return f"Error occurred during the request: {err}"
        return request_metadata.json()

    async def bulk_download(self):
        """TODO"""
        raise NotImplementedError


async def main():
    """TODO"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--metadata",
        action="store_true",
        help="Get the metadata from alphafold, the list contains all the archive files available for bulk download.",
    )
    parser.add_argument(
        "-r",
        "--readme",
        action="store_true",
        help="Get the readme from alphahold ftp server",
    )
    afdb = AFDB()
    args = parser.parse_args()
    if args.metadata:
        pprint(await afdb.get_metadata_json())
    elif args.readme:
        print(await afdb.get_readme())


if __name__ == "__main__":
    asyncio.run(main())
